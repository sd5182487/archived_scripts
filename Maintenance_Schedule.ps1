<# 
if you want to create a maintenance of app Y(app name) in X(environment) using Z(template name *.cvs) with script S
the input would be like this:    .\S 'X' 'Y\Z'

e.g. :
.\ScheduleTest.ps1 'dev' 'HypericSchedulesExample\TestSchedule.csv'

And the log file will show in HypericSchedulesExample\TestSchedule.log
#>



param(	
	[string]$env, [string]$Template
)


$log = $Template -replace ".csv", ".log"

$CSVLocation = '\\gmo\'+ $env +'\App\Hqapi\HypericSchedules\'+ $Template;
$LogLocation = '\\gmo\'+ $env +'\App\Hqapi\HypericSchedules\'+ $log

write-host $CSVLocation 


try{stop-transcript|out-null}
catch [System.InvalidOperationException]{}
#Start-Transcript -Path $LogLocation;

cd \\gmo\prd\App\Hqapi\hqapi1-client-5.0.0\bin\GMO_Scripts;


$rawinput = Import-Csv $CSVLocation;
$Date = Get-Date;
$Day = $date.DayOfWeek;

function DailySet{
param([string]$ServiceID, [string]$Daily, [string]$DStartTime, [string]$DEndTime)
 if($Daily -match 'Y'){
    if($DEndTime -match 'PM'){
        $StartToday = $Date.ToShortDateString() + ' ' + $DStartTime;
        $EndToday = $Date.ToShortDateString() + ' ' + $DEndTime;
        [string]$check = .\hqapi.ps1 maintenance get --resourceId $ResourceID;
        if ($check -match 'new'){
			.\hqapi.ps1 maintenance unschedule --resourceId $ResourceID;
            .\hqapi.ps1 maintenance schedule --resourceId $ResourceID --start $StartToday --end $EndToday;
            .\hqapi.ps1 maintenance get --resourceId $ResourceID;
            <#DEBUG .\hqapi.ps1 maintenance unschedule --resourceId $ServiceID; #>
        }elseif($check -match 'No maintenance events found'){
            #check start time of schedule against current time
            if([datetime]$DStartTime -gt (get-date)){
                .\hqapi.ps1 maintenance schedule --resourceId $ResourceID --start $StartToday --end $EndToday;
                .\hqapi.ps1 maintenance get --resourceId $ResourceID;
                <#DEBUG .\hqapi.ps1 maintenance unschedule --resourceId $ServiceID; #>
            }else{
            write-host "ERROR: $ServiceID cannot be scheduled!";
            write-host "       Please run this script before $DStartTime";
            }
        }   
    }
    elseif($DEndTime -match 'AM'){
        $StartToday = $Date.ToShortDateString() + ' ' + $DStartTime;
        $EndTomorrow = $Date.AddDays(1).ToShortDateString() + ' ' + $DEndTime;
        [string]$check = .\hqapi.ps1 maintenance get --resourceId $ResourceID;
        if ($check[1] -match 'new'){
            .\hqapi.ps1 maintenance unschedule --resourceId $ResourceID
            .\hqapi.ps1 maintenance schedule --resourceId $ResourceID --start $StartToday --end $EndTomorrow;
            .\hqapi.ps1 maintenance get --resourceId $ResourceID;
            <#DEBUG .\hqapi.ps1 maintenance unschedule --resourceId $ServiceID; #>
        }elseif($check -match 'No maintenance events found'){
            if([datetime]$DStartTime -gt (get-date)){
                .\hqapi.ps1 maintenance schedule --resourceId $ResourceID --start $StartToday --end $EndTomorrow;
                .\hqapi.ps1 maintenance get --resourceId $ResourceID;
                <#DEBUG .\hqapi.ps1 maintenance unschedule --resourceId $ServiceID; #>
            }else{
            write-host "ERROR: $ServiceID cannot be scheduled!";
            write-host "       Please run this script before $DStartTime";
            }
        }  
    }
 }
}

function WeekendSet{
param([string]$ServiceID, [string]$WStartDay, [string]$WStartTime, [string]$WEndDay, [string]$WEndTime)

$ScheduleStartDay = $date;
$ScheduleEndDay = $date;
if($WStartDay -match 'Fri'){$ScheduleStartDay = $ScheduleStartDay.ToShortDateString() + ' ' + $wStartTime}
elseif ($WStartDay -match 'Sat'){$ScheduleStartDay = $ScheduleStartDay.AddDays(1).ToShortDateString() + ' ' + $wStartTime;}
elseif ($WStartDay -match 'Sun'){$ScheduleStartDay = $ScheduleStartDay.AddDays(2).ToShortDateString() + ' ' + $wStartTime;} #Just in case

if ($WEndDay -match 'Sat'){$ScheduleEndDay = $ScheduleEndDay.AddDays(1).ToShortDateString() + ' ' + $wEndTime;} #Just in case
elseif ($WEndDay -match 'Sun'){$ScheduleEndDay = $ScheduleEndDay.AddDays(2).ToShortDateString() + ' ' + $wEndTime;}
elseif ($WEndDay -match 'Mon'){$ScheduleEndDay = $ScheduleEndDay.AddDays(3).ToShortDateString() + ' ' + $wEndTime;}

        .\hqapi.ps1 maintenance schedule --resourceId $ResourceID --start $ScheduleStartDay --end $ScheduleEndDay;
        .\hqapi.ps1 maintenance get --resourceId $ResourceID;
        <#DEBUG .\hqapi.ps1 maintenance unschedule --resourceId $ServiceID; #>
}


# Reads each row in CSV
foreach ($row in $rawinput){
    [string]$ServerName = $row.ServerName;
    [string]$ServiceName = $row.ServiceName;
    [string]$WStartDay = $row.WeekendStartDay;
    [string]$WStartTime = $row.WeekendStartTime;
    [string]$WEndDay = $row.WeekendEndDay;
    [string]$WEndTime = $row.WeekendEndTime;
    [string]$Daily = $row.DailyDowntime;
    [string]$DStartTime = $row.DailyStartTime;
    [string]$DEndTime = $row.DailyEndTime;

	#$ResourceMachineName = "`"$ServerName`_"; # Add " and _ to string
    if($ServerName -notmatch '.gmo.tld'){$Machine = $ServerName + '.gmo.tld';}
	#$ResourceMachineName = "`"$Machine`_"; # Add " and _ to string

    #Fill ServiceName spaces with underscores
    $MachineService = $ServiceName | %{$_ -replace " ", "_"}|%{$_ -replace "-", '_'} | %{$_ -replace '___', '_'} | %{$_ -replace '__', '_'}
    #Use MachineService to find Service's ID (only visible in XML)
	#$ResourceServiceName = "$MachineService`""
	$ServiceID = .\hqapi.ps1 resource list --platform $Machine --children | where {$_ -match $MachineService} |sort-object|select-object -last 1 | %{$_ -replace , '.*ce id="(\d+)".*', '$1'}
	
	[int]$ResourceID = $ServiceID;
    if(!($ServiceID -match '^\d*$')){
        write-error "ERROR: No Service ID for $MachineService on $Machine";
    }else{

        if($Day -eq 'Monday' -or $Day -eq 'Tuesday' -or $Day -eq 'Wednesday' -or $Day -eq 'Thursday'){
            DailySet $ServiceID $Daily $DStartTime $DEndTime;
            if ($daily -eq 'Y'){write-host "Successfully scheduled $Day Maintenance for $ServiceName`n";}
        }
        elseif($Day -eq 'Friday'){
            WeekendSet $ServiceID $WStartDay $WStartTime $WEndDay $WEndTime;
            write-host "Successfully scheduled Weekend Maintenance for $ServiceName`n";
        }
    }
}

#Stop-Transcript;
$log = Get-Content $LogLocation | Select-String -pattern "log4j:WARN" -notmatch;
$log | Set-Content $LogLocation;

#Write-Host "Schedule complete: Output viewable at $LogLocation";
cd \\gmo\prd\App\Hqapi\HypericSchedules\;
